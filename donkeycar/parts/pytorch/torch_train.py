import os
from pathlib import Path
import torch
import pytorch_lightning as pl
from donkeycar.parts.pytorch.torch_data import TorchTubDataModule
from donkeycar.parts.pytorch.torch_utils import get_model_by_type


def train(cfg, tub_paths, model_output_path, model_type):
    """
    Train the model
    """
    model_name, model_ext = os.path.splitext(model_output_path)

    is_torch_model = model_ext == '.ckpt'
    if is_torch_model:
        model = f'{model_name}.ckpt'

    if not model_type:
        model_type = cfg.DEFAULT_MODEL_TYPE

    tubs = tub_paths.split(',')
    tub_paths = [os.path.expanduser(tub) for tub in tubs]
    output_path = os.path.expanduser(model_output_path)
    train_type = 'linear' if 'linear' in model_type else model_type

    output_dir = Path(model_output_path).parent

    model = get_model_by_type(train_type, cfg)

    if torch.cuda.is_available():
        print('Using CUDA')
        gpus = -1
    else:
        print('Not using CUDA')
        gpus = 0

    logger = None
    if cfg.VERBOSE_TRAIN:
        from pytorch_lightning.loggers import TensorBoardLogger

        # Create Tensorboard logger
        logger = TensorBoardLogger('tb_logs', name='DonkeyNet')


    cfg.MAX_EPOCHS = 3
    weights_summary = 'full' if cfg.PRINT_MODEL_SUMMARY else 'top'
    trainer = pl.Trainer(gpus=gpus, logger=logger, progress_bar_refresh_rate=30,
                         max_epochs=cfg.MAX_EPOCHS, default_root_dir=output_dir, weights_summary=weights_summary)

    data_module = TorchTubDataModule(cfg, tub_paths)
    trainer.fit(model, data_module)

    if is_torch_model:
        checkpoint_model_path = f'{os.path.splitext(output_path)[0]}.ckpt'
        trainer.save_checkpoint(checkpoint_model_path)
        print("Saved final model to {}".format(checkpoint_model_path))

    return None
